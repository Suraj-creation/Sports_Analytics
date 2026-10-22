/**
 * Navigation shims.
 *
 * TanStack Router's typed navigation hangs off a single global `Register` interface,
 * and the production app at src/router.tsx already claims it. Declaring a second one
 * is a type error, and leaving the production one in place would type every prototype
 * route against the production route tree.
 *
 * Rather than touch a production file for a design prototype, the prototype re-exports
 * the same runtime hooks with their route-literal typing erased. Runtime behaviour —
 * the route tree, search validation, scroll restoration, deep links — is unchanged;
 * only compile-time route autocompletion is given up, which is the cheaper loss here.
 */

import {
  Link as RouterLink,
  useNavigate as useRouterNavigate,
  useParams as useRouterParams,
  useSearch as useRouterSearch,
} from "@tanstack/react-router";
import type { ComponentType, ReactNode } from "react";

type AnyRecord = Record<string, unknown>;

export interface LinkProps {
  to: string;
  params?: AnyRecord;
  search?: AnyRecord;
  className?: string;
  children?: ReactNode;
  title?: string;
  "aria-current"?: "page" | "step" | undefined;
  "aria-label"?: string;
}

export const Link = RouterLink as unknown as ComponentType<LinkProps>;

export function useNavigate(): (opts: {
  to: string;
  params?: AnyRecord;
  search?: AnyRecord;
  replace?: boolean;
}) => void {
  return useRouterNavigate() as never;
}

export function useSearch<T extends object>(opts: { from: string }): T {
  return useRouterSearch(opts as never) as T;
}

export function useParams<T extends object>(opts: { from: string }): T {
  return useRouterParams(opts as never) as T;
}
